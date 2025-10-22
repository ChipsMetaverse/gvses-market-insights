# 🚨 ChatKit Iframe Not Rendering - Production Issue

## Executive Summary
**The ChatKit iframe is receiving a session and control object, but the iframe content is not being displayed in production.** The logs show successful initialization, but visually there's only white space where the ChatKit interface should be.

## Evidence

### Console Logs (Working):
```
✅ ChatKit session established with Agent Builder
🎮 [RealtimeChatKit] Control received from ChatKit hook (first time)
✅ RealtimeChatKit initialized with Agent Builder integration
🎮 [Dashboard] ChatKit control is now ready for message sending
🔄 [ChatKit] State changed: {ready: true, error: null, hasControl: true}
```

### Visual Evidence (NOT Working):
Screenshot shows:
- "AI Trading Assistant" header ✅
- Microphone icon ✅  
- "Voice Commands" button ✅
- **NO ChatKit iframe** ❌ - just white space
- **NO "What can I help with today?" prompt** ❌
- **NO input field** ❌

### Playwright Snapshot Evidence:
Earlier snapshot showed the iframe WITH content:
```yaml
- iframe [ref=e107]:
  - generic [ref=f1e4]:
    - main [ref=f1e12]:
      - heading "What can I help with today?" [level=2]
    - generic [ref=f1e19]:
      - textbox "Message the AI" [active]
```

But current snapshots show the iframe exists but is EMPTY or not rendered.

## Root Cause Hypotheses

###  Hypothesis 1: CSS/Z-Index Issue
The iframe might be:
- Behind other elements
- Opacity set to 0
- Display: none
- Height: 0

### Hypothesis 2: React Rendering Race Condition
The ChatKit component might be:
- Mounting/unmounting rapidly (infinite loop remnants?)
- Not receiving proper props
- iframe src not loading

### Hypothesis 3: OpenAI ChatKit Library Issue
The `useChatKit` hook might be:
- Returning control but not rendering UI
- Failing silently in production build
- Missing configuration

### Hypothesis 4: Content Security Policy (CSP)
Production might have stricter CSP blocking iframe content.

## Investigation Steps Required

### Step 1: Check ChatKit Component Props
```bash
# Log the actual ChatKit component in RealtimeChatKit.tsx
console.log('ChatKit iframe props:', { 
  control: chatKitControl, 
  className, 
  style 
});
```

### Step 2: Check if iframe src is set
```bash
# In browser DevTools
document.querySelector('iframe').src
# Should be OpenAI ChatKit URL
```

### Step 3: Check CSS on iframe
```bash
# Check computed styles
const iframe = document.querySelector('iframe');
console.log(window.getComputedStyle(iframe));
```

### Step 4: Check for JavaScript Errors
Look for:
- `@openai/chatkit-react` errors
- CORS errors
- CSP violations

## Files to Check

1. **frontend/src/components/RealtimeChatKit.tsx** (lines 333-357)
   - ChatKit component rendering
   - iframe props
   - control object

2. **frontend/src/components/TradingDashboardSimple.tsx** (lines 1780-1787)
   - RealtimeChatKit wrapper
   - Panel styling

3. **frontend/src/components/TradingDashboardSimple.css** (voice-panel-right)
   - Panel height/width
   - Overflow settings

## Temporary Workaround

Since the control object IS available (`chatKitControl.sendMessage` works in logs), we could:
1. Build a custom text input UI
2. Use chatKitControl.sendMessage() directly
3. Display responses in a custom message list

But this defeats the purpose of using ChatKit's Agent Builder workflow UI.

## Next Steps

1. ✅ Remove usage hints footer (DONE - confirmed space issue resolved)
2. ❌ **Investigate why iframe isn't rendering despite successful session**
3. Check browser console in production for errors
4. Verify `@openai/chatkit-react` version compatibility
5. Check if ChatKit iframe needs specific dimensions
6. Test with simpler ChatKit config

## Success Criteria

- ✅ Session established
- ✅ Control object received
- ✅ No infinite render loop
- ❌ **ChatKit UI visible in iframe**
- ❌ **Input field functional**

**STATUS: 3/5 criteria met. Core functionality works but UI doesn't render.**

