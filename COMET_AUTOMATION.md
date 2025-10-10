# Comet Browser Automation with Native Features

## Problem
Standard Playwright automation disables Comet's native features (Assistant, widgets, etc.) because it launches with `--enable-automation` flags.

## Solutions

### ✅ Solution 1: AppleScript Control (RECOMMENDED)
**100% Native Features Preserved**

Uses macOS AppleScript to control Comet like a human user would. No browser automation flags.

```javascript
const { CometController } = require('./comet_applescript_control.js');
const comet = new CometController();

// Basic operations
comet.launch();                           // Open Comet
comet.newTab();                           // Cmd+T
comet.navigateTo('localhost:5175');       // Navigate
comet.toggleAssistant();                  // Cmd+A
comet.sendToAssistant('Your question');   // Type and Enter
comet.summarizePage();                    // Cmd+S
comet.screenshot('output.png');           // Take screenshot
```

**Pros:**
- ✅ All native features work (Assistant, widgets, etc.)
- ✅ Acts exactly like human interaction
- ✅ No browser modifications
- ✅ Can interact with any UI element

**Cons:**
- ⚠️ Requires macOS
- ⚠️ Limited to keyboard/mouse simulation
- ⚠️ Cannot access page internals (DOM, etc.)

---

### ✅ Solution 2: CDP Monitoring
**Native Features + Some Monitoring**

Launches Comet with only `--remote-debugging-port`, connects via Chrome DevTools Protocol.

```bash
node comet_native_with_monitoring.js
```

**Features:**
- Monitors console logs
- Tracks page navigation
- Injects monitoring scripts
- Listens for new tabs/windows

**Pros:**
- ✅ Preserves most native features
- ✅ Can monitor internal browser state
- ✅ Can inject scripts
- ✅ Tracks console output

**Cons:**
- ⚠️ Some native features may be affected
- ⚠️ More complex setup

---

## Hybrid Approach (BEST)

Combine both methods:

```javascript
const { chromium } = require('playwright');
const { CometController } = require('./comet_applescript_control.js');

async function hybridAutomation() {
  // 1. Use AppleScript for UI interactions (preserves native features)
  const comet = new CometController();
  comet.launch();
  await sleep(2000);
  
  comet.navigateTo('localhost:5175');
  await sleep(3000);
  
  // 2. Connect CDP for monitoring/data extraction
  const browser = await chromium.connectOverCDP('http://localhost:9223');
  const context = browser.contexts()[0];
  const page = context.pages()[0];
  
  // 3. Monitor with CDP
  page.on('console', msg => console.log('Browser:', msg.text()));
  
  // 4. Interact with AppleScript
  comet.toggleAssistant();
  comet.sendToAssistant('Analyze this dashboard');
  
  // 5. Extract data with CDP
  await sleep(5000);
  const response = await page.evaluate(() => {
    return document.querySelector('.assistant-response')?.textContent;
  });
  
  console.log('Assistant said:', response);
}
```

---

## Use Cases

### Monitor Assistant While Preserving Features
```javascript
const comet = new CometController();

// Navigate and interact naturally
comet.navigateTo('https://example.com');
await sleep(2000);

// Use Assistant (native features intact)
comet.toggleAssistant();
comet.sendToAssistant('What is this page about?');

// CDP monitoring script will log responses
```

### Automate Complex Web Tasks
```javascript
const comet = new CometController();

// Assistant can handle complex web interactions
comet.toggleAssistant();
comet.sendToAssistant('Find all product prices on this page and compare them');

// CDP monitors the task
// Assistant uses native web scraping capabilities
```

### Screenshot + Analysis Loop
```javascript
const comet = new CometController();

for (const url of urls) {
  comet.navigateTo(url);
  await sleep(3000);
  
  comet.screenshot(`page_${i}.png`);
  
  comet.summarizePage(); // Cmd+S
  await sleep(2000);
  
  // Save summary...
}
```

---

## Quick Start

### 1. AppleScript Only (Simplest)
```bash
node comet_applescript_control.js --demo
```

### 2. CDP Monitoring
```bash
# Terminal 1: Start monitoring
node comet_native_with_monitoring.js

# Terminal 2: Use Comet normally
# Monitoring script will log Assistant activity
```

### 3. Full Integration
See `examples/` folder for complete examples.

---

## API Reference

### CometController Methods

| Method | Description | Example |
|--------|-------------|---------|
| `launch()` | Open Comet | `comet.launch()` |
| `newTab()` | Cmd+T | `comet.newTab()` |
| `navigateTo(url)` | Navigate to URL | `comet.navigateTo('localhost:5175')` |
| `toggleAssistant()` | Cmd+A | `comet.toggleAssistant()` |
| `summarizePage()` | Cmd+S | `comet.summarizePage()` |
| `sendToAssistant(text)` | Type and send | `comet.sendToAssistant('Hello')` |
| `screenshot(file)` | Capture | `comet.screenshot('out.png')` |
| `isRunning()` | Check status | `if (comet.isRunning())` |
| `getWindowInfo()` | Window names | `comet.getWindowInfo()` |

---

## Why This Works

### Standard Playwright (Native Features Disabled)
```bash
chromium.launch({ executablePath: 'Comet' })
# Launches with: --enable-automation --disable-extensions ...
# Result: Native features disabled ❌
```

### Our AppleScript Approach (Native Features Intact)
```bash
open -a Comet
osascript -e 'tell System Events to keystroke "a" using command down'
# No automation flags, just simulates user input
# Result: Native features work ✅
```

### Our CDP Approach (Mostly Intact)
```bash
/Applications/Comet.app/Contents/MacOS/Comet --remote-debugging-port=9223
# Only debugging port, no automation flags
# Result: Native features mostly work ✅
```

---

## Testing

Run the test suite:
```bash
npm test
# Or manually:
node comet_applescript_control.js --demo
```

---

## Troubleshooting

**"Comet not responding to commands"**
- Ensure Comet has Accessibility permissions
- System Settings > Privacy & Security > Accessibility > Add Terminal

**"CDP connection failed"**
- Make sure no other debugging sessions are active
- Try: `pkill -9 Comet && node comet_native_with_monitoring.js`

**"Screenshot not working"**
- Grant Screen Recording permissions
- System Settings > Privacy & Security > Screen Recording > Add Terminal

---

## Advanced: Custom Actions

```javascript
// Create custom automation
class MyAutomation extends CometController {
  async analyzeStock(symbol) {
    this.navigateTo('localhost:5175');
    await this.wait(3000);
    
    this.toggleAssistant();
    this.sendToAssistant(`Analyze ${symbol} stock`);
    await this.wait(5000);
    
    this.screenshot(`${symbol}_analysis.png`);
  }
}

const auto = new MyAutomation();
await auto.analyzeStock('AAPL');
```

---

## Summary

✅ **AppleScript**: Best for preserving native features  
✅ **CDP**: Best for monitoring and data extraction  
✅ **Hybrid**: Best for complex automation + monitoring  

All methods allow you to use Comet's Assistant with its full web-scraping and analysis capabilities intact!

