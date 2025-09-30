# Debug Vision Tools

These tools use OpenAI's Computer Use Preview model to help debug your application by taking screenshots and analyzing what you see during testing.

## Tools Created

### 1. `debug_vision_tool.py` - General Screen Analysis
Takes screenshots of your entire screen/desktop and analyzes them.

**Usage:**
```bash
# Take a screenshot and analyze current state
python debug_vision_tool.py --screenshot

# Debug with specific context
python debug_vision_tool.py --help-debug "agent not responding to queries"

# Continuous monitoring mode
python debug_vision_tool.py --monitor --interval 10
```

### 2. `browser_debug_tool.py` - Web Application Debugging
Specifically designed for debugging web applications using Playwright + Computer Use.

**Usage:**
```bash
# Debug a specific issue
python browser_debug_tool.py --url http://localhost:5174 --debug "query not working"

# Test a specific agent query
python browser_debug_tool.py --test-query "What is everything down?"

# Monitor application continuously
python browser_debug_tool.py --monitor-app --interval 15
```

## Setup Requirements

### 1. Install Dependencies
```bash
pip install openai playwright
npx playwright install chromium
```

### 2. Set OpenAI API Key
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Ensure Computer Use Access
You need access to OpenAI's Computer Use Preview model (`computer-use-preview`).

## How It Helps Debug Your Issue

### For the "Downeverything" Query Issue:

1. **Real-time Analysis**: I can see exactly what you see in your browser
2. **UI State Detection**: Identify if buttons are disabled, forms aren't working, etc.
3. **Error Message Capture**: Spot console errors or UI error messages
4. **Response Analysis**: See if the agent is responding but with wrong data
5. **Network Issues**: Identify loading states or failed requests

### Example Debugging Session:

```bash
# Start monitoring your app while you test
python browser_debug_tool.py --monitor-app --url http://localhost:5174

# Or debug the specific issue
python browser_debug_tool.py --debug "agent responds to 'select' queries but not 'downeverything' queries" --url http://localhost:5174

# Test the problematic query directly
python browser_debug_tool.py --test-query "What is everything down?" --url http://localhost:5174
```

## What I Can See and Analyze

✅ **Browser interface state**
✅ **Form inputs and buttons**
✅ **Loading indicators**
✅ **Error messages**
✅ **Console output (if visible)**
✅ **Network request states**
✅ **Chart displays**
✅ **Agent responses**
✅ **UI component states**

## Benefits for Your Testing

1. **Visual Debugging**: I can see exactly what you see
2. **Automated Analysis**: Computer Use model analyzes screenshots intelligently
3. **Continuous Monitoring**: Track changes over time
4. **Specific Query Testing**: Test problematic queries automatically
5. **Cross-Reference**: Compare working vs non-working states

## Example Output

When you run the tool, you'll get detailed analysis like:

```
DEBUGGING ANALYSIS
============================================================
URL: http://localhost:5174
Title: Trading Dashboard

Analysis:
The application shows a trading dashboard with a chat interface. I can see:

1. Query input field is present and active
2. Previous messages show successful responses to "select" queries
3. When testing "What is everything down?" query:
   - Input field accepts the text
   - Submit button is clickable
   - However, no response appears in the chat
   - No loading indicator is shown
   - Console may show errors (check browser dev tools)

Suggestions:
- Check browser console for JavaScript errors
- Verify backend logs for query processing
- Test API endpoint directly with curl
- Check if symbol extraction is working for this query type
```

This gives me the visual context I need to help solve your "Downeverything" query issue effectively!
